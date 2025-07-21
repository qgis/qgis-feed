
#let
#  #
#  # Note that I am using a specific version from NixOS here because of
#  # https://github.com/NixOS/nixpkgs/issues/267916#issuecomment-1817481744
#  #
#  nixpkgs = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-22.11.tar.gz";
#  #nixpkgs = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/51f732d86fac4693840818ad2aa4781d78be2e89.tar.gz";
#  pkgs = import nixpkgs { config = { }; overlays = [ ]; };
#  pythonPackages = pkgs.python311Packages;
with import <nixpkgs> {}; let
  # For packages pinned to a specific version
  #pinnedHash = "617579a787259b9a6419492eaac670a5f7663917";
  #pinnedPkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/${pinnedHash}.tar.gz") {};
  pinnedPkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
  }) {};
in
  pkgs.mkShell rec {
    allowUnfree = true;
    buildInputs = [
      vscode
      pinnedPkgs.pre-commit
    ];

    shellHook = ''
      # Set up pre-commit hook if .pre-commit-config.yaml exists
      if [ -f .pre-commit-config.yaml ]; then
        if [ ! -d .git ]; then
          echo "No .git directory found, skipping pre-commit install."
        else
          pre-commit install
          echo "pre-commit hook installed."
        fi
      fi
      echo "QGIS Feed"
      echo "_________________________________________________________"
      echo "Command : Description"
      echo "_________________________________________________________"
      echo "🚀 ./vscode.sh          : Open VSCode"

    '';
  }
