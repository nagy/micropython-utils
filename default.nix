{
  pkgs ? import <nixpkgs> { },
  lib ? pkgs.lib,
  micropython ? pkgs.micropython,
}:

{
  default = micropython.overrideAttrs {
    preBuild = ''
      cp ${lib.cleanSource ./.}/echoservice.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/espnserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/tcpserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/udpserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/router.py ports/esp32/modules/
    '';
  };

  tests = pkgs.testers.runNixOSTest ({
    name = "micropython-utils-test";
    # flowchart LR
    #    A["⒈ TCP-L:8083"] <-->|UDP| B["⒉ Middle box, 50% drop rate"]
    #    B <-->|UDP| C["⒊ 🪞 Mirror"]
    nodes =
      let
        mkMachineWithRouteTable =
          {
            codes ? [ ],
            ...
          }@args:
          (lib.mkMerge [
            {
              environment.systemPackages = [
                micropython
                pkgs.curl
                pkgs.socat
              ];
              # networking.firewall.allowedTCPPorts = [ 8083 ];
              # networking.firewall.allowedUDPPorts = [ 3001 3002 ];
              networking.firewall.enable = false;
              networking.enableIPv6 = false;
              systemd.services.service_under_test = {
                wantedBy = [ "multi-user.target" ];
                serviceConfig = {
                  DynamicUser = true;
                  WorkingDirectory = lib.cleanSource ./.;
                  ExecStart = lib.escapeShellArgs (
                    [
                      "${micropython}/bin/micropython"
                      "test.py"
                    ]
                    ++ codes
                  );
                };
              };
            }
            (builtins.removeAttrs args [ "codes" ])
          ]);
      in
      {
        first = mkMachineWithRouteTable {
          systemd.services.capture = {
            wantedBy = [ "network.target" ];
            serviceConfig.ExecStart = ''
              ${pkgs.wireshark-cli}/bin/tshark -i lo -i eth1 -f 'tcp or udp' -w /var/lib/first.pcap
            '';
          };
          codes = [
            "tcpserver.create_task(8083,route)"
            "udpserver.create_task(3001,route)"
            "route[3003]=udpserver.make_udp_sender(3002,'second')"
            "route[3334]=route[3003]"
          ];
        };
        second = mkMachineWithRouteTable {
          codes = [
            "udpserver.create_task(3002,route)"
            "route[3003]=udpserver.make_udp_sender(3003, 'third')"
            "route[3334]=route[3003]"
            "route.fallback=udpserver.make_udp_sender(3001, 'first')"
          ];
        };
        third = mkMachineWithRouteTable {
          codes = [
            "udpserver.create_task(3003,route)"
            "route[3003]=echoservice.echo_service"
            "route[3334]=pingservice.make_pinger_service(route)"
            "route.fallback=udpserver.make_udp_sender(3002, 'second')"
          ];
        };
      };
    testScript = ''
      start_all()
      first.wait_for_unit("default.target")
      second.wait_for_unit("default.target")
      third.wait_for_unit("default.target")
      first.sleep(10) # needed for tshark
      first.succeed("timeout 10 nc localhost 8083 <<< \"3003\nfba20efd7e7b4343b8f7c4107fd7f0f4\"||true")
      first.sleep(10) # needed for tshark
      first.systemctl("stop capture.service")
      first.copy_from_vm("/var/lib/first.pcap")
    '';
  });
}
