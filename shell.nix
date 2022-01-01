mkShell {
  buildInputs = [
    git
    gitAndTools.gh

    python39Full
    python39Packages.pip

    python39Packages.click
    python39Packages.pillow
  ];

  shellHook = ''
    LOCALPATH="$(pwd)/.local"
    export PYTHONPATH="$LOCALPATH:$PYTHONPATH"
    mkdir -p .local
    pip3 install igramscraper --target="$LOCALPATH"
    cd -
  '';
}
