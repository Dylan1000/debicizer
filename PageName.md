TODO


---

NEW:

---


1. Icons:

a) Create Icons dir containing all App icons with the names bundleIdentifier.png

b) Packages with no icon must refer to a generic icon

c) Themes and some specific sections should have a specific generic icon

2. Prefix all exec and execnoerror with /usr/libexec/cydia/exec

3. Fix ignore apps without Uninstall scripts

4. Clean up metadata.py - remove all the prints


---


activate flag on copy path only in install - DONE

preflight


postflight Transit-0.27.04.zip

repair removepath (for uninstall) macalc (flag as copypath in install) - DONE

repair exec - maybe done need test

repair if

ifnot


alpha.xml:          

&lt;array&gt;



&lt;string&gt;

Exec

&lt;/string&gt;



&lt;string&gt;

/usr/libexec/cydia_/symlink libpcrecpp.0.0.0.dylib /usr/lib/libpcrecpp.dylib

&lt;/string&gt;



&lt;/array&gt;_


before add a script in removepath test if it's in the package (cp the files on read maybe?)
rm -rf "/private/var/root/Library/Preferences/Transit/busguides.db" -DONE

-if fileexist with a list of arguments MACalc-0.1.6.zip- DONE