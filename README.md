# html2nix

Converts `bookmarks.html` file as exported by a browser, only Firefox has been tested, into Nix syntax as accepted by Home Manager's `programs.firefox.profiles.<name>.bookmarks`.

# Running On Nix

- Clone this repo to your local Nix machine.
- From the root of the repo, run `nix-shell`.
- Run `python3 src/Html2Nix.py`:
    - Use `-i`/`--input` to define a input file.
    - Use `-o`/`--output` to define an output file.

# Output Usage

In a Home Manager Nix file, many name there's `home.nix`, set Firefox bookmarks as seen bellow:

```nix
programs.firefox.profiles.<name>.bookmarks = <html2nixOutputHere>;
```

OR

```nix
programs.firefox.profiles.<name>.bookmarks = import <pathToOutputFile>;
```

