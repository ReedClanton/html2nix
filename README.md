# html2nix

Convers bookmarks.html Firefox export into Nix syntax as accepted by Home Manager's programs.firefox.profiles.&lt;name>.bookmarks

# Running On Nix

- Clone this repo to your local Nix machine.
- Place your `bookmarks.html` file as exported by Firefox in the `<repoRoot>/inputs/` directory.
- From the root of the repo, run `shell-nix`.
- A `bookmarks.nix` file should be written to the root of the repo's directory. This file contains a Nix representation of your `bookmarks.html` file.

# Output Usage

In a Home Manager Nix file, many name there's `home.nix`, set Firefox bookmarks as seen bellow:

```
programs.firefox.profiles.<name>.bookmarks = [
    <html2nixOutputHere>
];
```

