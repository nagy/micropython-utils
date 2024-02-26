{ pkgs ? import <nixpkgs> { }
, lib ? pkgs.lib
, micropython ? pkgs.micropython
}:

micropython.overrideAttrs {
  preBuild = ''
    cp ${lib.cleanSource ./.}/aio_espnow_gateway.py ports/esp32/modules/
    cp ${lib.cleanSource ./.}/message_router.py     ports/esp32/modules/
  '';
}
