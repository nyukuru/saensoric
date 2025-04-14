{
  description = "Programming language for Instruments";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11-small";

  outputs = {nixpkgs, self, ...}: let
    # TODO; this should be all systems that support
    # latest python interpreter
    systems = [
      "x86_64-linux"
    ];

    forAllSystems = func: 
      nixpkgs.lib.genAttrs systems
        (system: (func system nixpkgs.legacyPackages.${system}));

    saensoric = {buildPythonApplication, setuptools, ...}: buildPythonApplication {
      pname = "saensoric";
      version = "0.0.0";

      src = ./.;

      build-system = [
        setuptools
      ];

    };

    in {
      packages = forAllSystems (system: pkgs: {
        default = self.packages.${system}.saensoric;
        saensoric = pkgs.callPackage saensoric;
      });

      devShells = forAllSystems (system: pkgs: {
        default = pkgs.callPackage ./shell.nix {};
      });
    };

}
