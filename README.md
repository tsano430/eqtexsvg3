**EQTeXSVG3**
============

EQTeXSVG3 is the fork of [EQTeXSVG][1].


Installation
------------

EQTeXSVG3 extension is meant to work with [Inkscape v1.0][2] (at the moment). 
It is composed of two files:

 - `eqtexsvg3.inx`: which is used by Inkscape to describe the extension
 - `eqtexsvg3.py`: which is the python script converting inline equation into SVG path

To install it, you need to replace existing files:

 - on Windows, in the following directory: `C:\Program Files\Inkscape\share\inkscape\extensions\`
 - on Ubuntu, in the following directory: `/usr/share/inkscape/extensions/`
 - on Mac, in the following directory: `/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions/`

Directories containing your softwares may depend on your configuration.


Needed tools
------------

This extension needs [TeX Live][3] to work properly. 
- Windows: [Installing TeX Live over the Internet][4]

- Ubuntu
```
$ sudo apt install texlive-full
```

- Mac ( If it doesn't work, please modify the line 20 in `eqtexsvg3.py` appropriately. )
```
$ brew cask install mactex
$ sudo tlmgr update --self --all
$ sudo tlmgr paper a4
```


Credits
--------

- `EqTeXSVG - LATEX Inkscape Extension`: https://www.julienvitard.eu/en/eqtexsvg_en.html
- `julienvitard/eqtexsvg`: https://github.com/julienvitard/eqtexsvg


[1]: https://github.com/julienvitard/eqtexsvg 
[2]: https://www.inkscape.org/
[3]: https://www.tug.org/texlive/
[4]: http://mirror.ctan.org/systems/texlive/tlnet/install-tl-windows.exe
