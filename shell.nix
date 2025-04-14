{
  mkShell,
  midivisualizer,
  midicsv,
  python313,
  muse,

}: mkShell {

  packages = [
    (python313.withPackages (python-pkgs: [
      python-pkgs.mido
    ]))
    midicsv
    midivisualizer
    muse
  ];
}
