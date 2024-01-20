# html2nix
Convers bookmarks.html Firefox export into Nix syntax as accepted by Home Manager's programs.firefox.profiles.&lt;name>.bookmarks

# Running On Nix

Create input directory, place your `bookmarks.html` file as exported from Firefox in it, run `shell-nix`, then `python3`, then `inport html2nix`. Copy output to between the `[` and `]` of Home Manager's `programs.firefox.profiles.<name>.bookmarks`.

