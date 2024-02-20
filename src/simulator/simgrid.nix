{ kapack ? import
    (fetchTarball "https://github.com/oar-team/nur-kapack/archive/05c3149d4dac2e3fee017907b412a8bea7693cbb.tar.gz")
  {}

}:

let
  pkgs = kapack.pkgs;
  
  my-python-packages = python-packages: with python-packages; [
    numpy
    matplotlib        
    # other python packages you want
  ]; 

  my-simgrid = kapack.simgrid-324.overrideAttrs(old: rec {
    version = "v3_13";
    src = kapack.pkgs.fetchgit rec {
      url = "https://framagit.org/Mema5/simgrid.git";
      rev = version;
      sha256 = "sha256-kFA/S+DzDPGXxmOVB5TmySOs5wyTtNAysVd5eBBw8Zc=";
    };
    patches = [];
    doCheck = false;
  });

in
  pkgs.mkShell {
        buildInputs = [          
          my-simgrid 
          (pkgs.python3.withPackages my-python-packages)
        ];
    }
