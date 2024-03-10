{ pkgs ? import <nixpkgs> { }
, lib ? pkgs.lib
, micropython ? pkgs.micropython }:

{
  default = micropython.overrideAttrs {
    preBuild = ''
      cp ${lib.cleanSource ./.}/printservice.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/echoservice.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/espnserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/tcpserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/udpserver.py ports/esp32/modules/
      cp ${lib.cleanSource ./.}/router.py ports/esp32/modules/
    '';
  };

  tests = pkgs.testers.runNixOSTest ({ ... }: {
    name = "micropython-utils-test";
    # flowchart LR
    #    A["⒈ TCP-L:8080"] <-->|UDP| B["⒉ Middle box, 50% drop rate"]
    #    B <-->|UDP| C["⒊ 🪞 Mirror"]
    nodes = let
      mkMachineWithRouteTable = { codes ? [], ... }@args:
        (lib.mkMerge [
          {
            environment.systemPackages = [ micropython pkgs.curl pkgs.socat ];
            # networking.firewall.allowedTCPPorts = [ 8083 ];
            # networking.firewall.allowedUDPPorts = [ 1111 2222 ];
            networking.firewall.enable = false;
            systemd.services.service_under_test = {
              wantedBy = [ "multi-user.target" ];
              serviceConfig = {
                DynamicUser = true;
                WorkingDirectory = lib.cleanSource ./.;
                ExecStart = lib.escapeShellArgs ([
                  "${micropython}/bin/micropython"
                  "test.py"
                ] ++ codes)
                ;
              };
            };
          }
          (builtins.removeAttrs args ["codes"])
        ]);
    in {
      first = mkMachineWithRouteTable {
        systemd.services.capture = {
          wantedBy = [ "network.target" ];
          serviceConfig.ExecStart = ''
            ${pkgs.wireshark-cli}/bin/tshark -i eth1 -w /var/lib/capture.pcap
          '';
        };
        codes = [
          "tcpserver.create_task(8083,_route_table)"
          "udpserver.create_task(1111,_route_table)"
          "_route_table[3333]=udpserver.make_udp_sender(2222,'second')"
        ];
      };
      second = mkMachineWithRouteTable { 
        codes = [
          "udpserver.create_task(2222,_route_table)"
          "_route_table[3333]=udpserver.make_udp_sender(3333, 'third')"
          "_route_table.fallback=udpserver.make_udp_sender(1111, 'first')"
        ];
      };
      third = mkMachineWithRouteTable { 
        codes = [
          "udpserver.create_task(3333,_route_table)"
          "_route_table[3333]=echoservice.make_echo_service(_route_table)"
          "_route_table.fallback=udpserver.make_udp_sender(2222, 'second')"
        ];
      };
    };
    testScript = ''
      start_all()
      first.wait_for_unit("default.target")
      second.wait_for_unit("default.target")
      third.wait_for_unit("default.target")
      first.sleep(10) # needed for tshark
      ...
      first.sleep(10) # needed for tshark
      first.systemctl("stop capture.service")
      first.copy_from_vm("/var/lib/capture.pcap")
    '';
  });

}
