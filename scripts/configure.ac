AC_INIT([open_pdks], [1.0], [github.com/RTimothyEdwards/open_pdks])

## REQUIRES: https://www.gnu.org/software/autoconf-archive/ax_python_module.html#ax_python_module
AM_PATH_PYTHON([3.4])
AX_PYTHON_MODULE([distutils],[])

realpath() {
    # Cross-platform, handles ~
    python3 -c 'import os,sys;print(os.path.realpath(os.path.expanduser(sys.argv@<:@1@:>@)))' $1
}

# detect PDKs based on directories that include Makefile.in files
m4_define([M4_GET_TECHS], [m4_normalize(m4_esyscmd(cd .. && find * -mindepth 1 -maxdepth 1 -name "Makefile.in" -exec dirname {} \; | tr "\n" " "))])

# define tools
# define tools to install setup files for.  This does not imply that the tools are
# available on the system;  just that open_pdks will install the setup files for them.
m4_define([M4_GET_TOOLS], [m4_normalize(m4_esyscmd(cat ./tools.txt | tr "\n" " "))])

# check for the source and install paths for each PDK.
AC_DEFUN([M4_GEN_WITH_PDK_ARGS], [

    # --enable-pdk-[pdk]=/path/to/pdk
    m4_foreach_w(pdk, $1, [
        echo "Checking technology pdk..."
        m4_define([pdkvar], [m4_normalize(m4_esyscmd(echo pdk | tr "a-z-" "A-Z_"))])

        pdkvar[]_SOURCE_PATH=""
        pdkvar[]_LOCAL_PATH=""
        pdkvar[]_DIST_PATH=""
        pdkvar[]_LINK_TARGETS="none"

        pdk_get() {
            AC_CHECK_FILE(../pdk/[pdk]_info.txt, [
                AC_CHECK_FILE(../sources/pdk,[
                    echo "Using pre-existing pdk download..."
                ], [
                    REPO=$(cat "../pdk/pdk_info.txt" | sed -n "1p")
                    POST_CLONE_COMMANDS=$(cat "../pdk/pdk_info.txt" | sed "1d")
                    mkdir -p ../sources
                    git clone "$REPO" ../sources/pdk;
                    (cd ../sources/pdk && sh -c "$POST_CLONE_COMMANDS")
                ])
                export pdkvar[]_SOURCE_PATH=../sources/pdk
            ], [
                AC_MSG_ERROR([PDK pdk cannot be automatically downloaded and requires a path.])
            ])
        }

        pdk_find() {
            FOUND=0
            for path in /opt/pdks/pdk /usr/share/pdks/pdk /usr/local/share/pdks/pdk; do
                if @<:@ -d $path @:>@ ; then
                    echo "Found pdk in $path, using this installation..."
                    export pdkvar[]_SOURCE_PATH=$path
                    FOUND=1
                fi
            done
            if @<:@ "$FOUND" = "0" @:>@; then
                echo "Could not find pdk in standard search paths, automatically fetching repository to ../sources/pdk ..."
                pdk_get
            fi
        }

        AC_ARG_ENABLE(pdk-[pdk],
            [AS_HELP_STRING([--enable-pdk-[pdk]=@<:@/path/to/pdk/@:>@ --disable-pdk-[pdk]], "location of the source files for the pdk (pdks with a [pdk]_url file can automatically download them if the path is omitted)")],
            [
                if test "$enableval" == "yes" -o "$enableval" == "YES"; then
		    echo "Looking for pdk in usual places"
                    pdk_find
                elif test "$enableval" == "no" -o "$enableval" == "NO"; then
                    echo "Disabling pdk..."
                else
                    pdkvar[]_SOURCE_PATH=$enableval
                fi
            ], [
            ]
        )
	    # # Require this argument

        if @<:@ "$[]pdkvar[]_SOURCE_PATH" != "" @:>@; then
            pdkvar[]_SOURCE_PATH=`realpath $[]pdkvar[]_SOURCE_PATH`
            pdkvar[]_BASENAME=`basename $[]pdkvar[]_SOURCE_PATH`
	    if @<:@ "$[]pdkvar[]_BASENAME" = "libraries" @:>@; then
		pdkvar[]_SOURCE_PATH=`dirname $[]pdkvar[]_SOURCE_PATH`
	    fi
            # basic check that the PDK exists there (the path must exist in any case)
            AC_MSG_NOTICE([Checking specified path for 'pdk' at $[]pdkvar[]_SOURCE_PATH])
            AC_CHECK_FILE($pdkvar[]_SOURCE_PATH,[
                AC_MSG_NOTICE(['pdk' source path found at $pdkvar[]_SOURCE_PATH])
            ], [
                AC_MSG_ERROR([Specified path for 'pdk' at $pdkvar[]_SOURCE_PATH not found])
            ])

            # --with-pdk-local-path=PDK_LOCAL_PATH
            AC_ARG_WITH(pdk-local-path,
                [AS_HELP_STRING([--with-pdk-local-path=/path/to/install/pdk], "run-time location of the PDK")],
                [pdkvar[]_LOCAL_PATH=$withval]
            )
            
            # Require this argument
            AC_MSG_NOTICE([Checking whether local path is specified for 'pdk'])
            if test "x$[]pdkvar[]_LOCAL_PATH" == "x" ; then
                AC_MSG_ERROR([Option --with-pdk-local-path=<path> not specified!])
                pdkvar[]_LOCAL_PATH=""
            else
                pdkvar[]_LOCAL_PATH=`realpath $[]pdkvar[]_LOCAL_PATH`
            fi

            # --with-pdk-dist-path=PDK_DIST_PATH
            AC_ARG_WITH(pdk-dist-path,
                [AS_HELP_STRING([--with-pdk-dist-path=/path/to/install/pdk], "staging location to install the PDK for distribution (optional)")],
                [pdkvar[]_DIST_PATH=$withval]
            )

            
            # "Require" this argument
            AC_MSG_NOTICE([Checking whether distribution path is specified for 'pdk'])
            if test "x$[]pdkvar[]_DIST_PATH" == "x" ; then
                AC_MSG_NOTICE([Option --with-pdk-dist-path=<path> not specified.  Local install only.])
                pdkvar[]_DIST_PATH=""
            else
                pdkvar[]_DIST_PATH=`realpath $[]pdkvar[]_DIST_PATH`
            fi

            # --with-pdk-link-targets=PDK_LINK_TARGETS
            AC_ARG_WITH(pdk-link-targets,
                [AS_HELP_STRING([--with-pdk-link-targets=none|source], "make symbolic links to existing files @<:@default=none@:>@")],
                [[]pdkvar[]_LINK_TARGETS=$with_[]pdk[]_link_targets]
            )
            AC_SUBST([]pdkvar[]_LINK_TARGETS)
            AC_MSG_NOTICE([Link targets set to $pdkvar[]_LINK_TARGETS])
        fi

        AC_SUBST(pdkvar[]_SOURCE_PATH)
        AC_SUBST(pdkvar[]_LOCAL_PATH)
        AC_SUBST(pdkvar[]_DIST_PATH)
        AC_SUBST(pdkvar[]_LINK_TARGETS)
    ])
])

AC_MSG_NOTICE([Found technology directories: M4_GET_TECHS()])

M4_GEN_WITH_PDK_ARGS(M4_GET_TECHS())

# Set variables for tool setups
AC_DEFUN([M4_GEN_WITH_TOOLS], [
    m4_foreach_w(tool, $1, [
        m4_define([toolvar], [m4_normalize(m4_esyscmd(echo tool | tr "a-z-" "A-Z_"))])

        toolvar[]_DISABLED=0
        AC_ARG_ENABLE(tool,
            AS_HELP_STRING(
                --enable-tool
                Enable or disable tool setup @<:@default=enabled@:>@
            ), [
                if test "$enableval" == "no" -o "$enableval" == "NO"; then
                    toolvar[]_DISABLED=1
                fi
            ]
        )
        AC_SUBST(toolvar[]_DISABLED)
    ])
])

AC_MSG_NOTICE([Found tools: M4_GET_TOOLS()])

M4_GEN_WITH_TOOLS(M4_GET_TOOLS())

# Magic
AC_PATH_PROG(MAGIC, magic)
if test -z "$MAGIC"; then
   AC_MSG_ERROR([You need 'magic' to generate the needed various cell views.])
fi
AC_PATH_PROG(PATCH, patch)
if test -z "$PATCH"; then
   AC_MSG_ERROR([You need 'patch' to apply patches.])
fi

# Other installations (libraries or tools if applicable)
AC_DEFUN([M4_GEN_INSTALLATION], [
    m4_define([target], $1)
    m4_define([targetvar], [m4_normalize(m4_esyscmd(echo target | tr "a-z-" "A-Z_"))])
    m4_define([flag], $2)
    m4_define([url], $3)
    m4_define([location], $4)

    # echo target targetvar flag url location

    targetvar[]_PATH=""
    targetvar[]_GET() {
        AC_CHECK_FILE(
            location/target,
            [
                echo "Using pre-existing target download..."
            ], [
                mkdir -p location/target
                sh ./download.sh url location/target.tar.gz
                (echo "Extracting target..." && cd location && tar -xf target.tar.gz --strip-components 1 -C location/target && rm target.tar.gz )
            ]
        )
        export targetvar[]_PATH=location/target
    }

    AC_ARG_ENABLE(
        flag,
        AS_HELP_STRING(
            [--enable-flag@<:@=path@:>@],
            [Install target. If path is omitted, it'll be downloaded. @<:@default=disabled@:>@]
        ), [
            if test "$enableval" == "yes" -o "$enableval" == "YES"; then
                targetvar[]_GET
                XSCHEM_INST=1
            elif test "$enableval" == "no" -o "$enableval" == "NO"; then
                echo "Disabling target..."
                XSCHEM_DISABLED=1
            else
                targetvar[]_PATH=$enableval
            fi
            targetvar[]_PATH=`realpath $[]targetvar[]_PATH`
        ],
        []
    )

    $5

    AC_SUBST(targetvar[]_PATH)
])

M4_GEN_INSTALLATION(sky130_ml_xx_hd, alpha-sky130, 'https://github.com/PaulSchulz/sky130_pschulz_xx_hd/archive/master.tar.gz', ../sources)

M4_GEN_INSTALLATION(xschem_sky130, xschem-sky130, 'https://github.com/StefanSchippers/xschem_sky130/archive/main.tar.gz', ../sources)

AC_DEFUN([M4_GEN_WITH_TOOLS], [
    m4_foreach_w(tool, $1, [
        m4_define([toolvar], [m4_normalize(m4_esyscmd(echo tool | tr "a-z-" "A-Z_"))])

        toolvar[]_DISABLED=0
        AC_ARG_ENABLE(tool,
            AS_HELP_STRING(
                --enable-tool --disable-tool,
                Enable or disable tool setup @<:@default=enabled@:>@
            ),
            [
                if test "$enableval" == "no" -o "$enableval" == "NO"; then
                    toolvar[]_DISABLED=1
                fi
            ],
        )
        AC_SUBST(toolvar[]_DISABLED)
    ])
])

AC_MSG_NOTICE([Tools enabled for PDK setup installation: M4_GET_TOOLS()])

# Check for "--with-ef-style"
EF_STYLE=0
AC_ARG_WITH(
    [ef-style],
    AS_HELP_STRING(
        [--with-ef-style],
        [Use efabless style file system structure @<:@default=no@:>@]
    ), [
        pdks_ef_style=$withval
        if test "$withval" == "yes" -o "$withval" == "YES"; then
            EF_STYLE=1
        fi
    ],
)

AC_SUBST(EF_STYLE)

MAKEFILES=$(find .. -name "Makefile.in" | sed 's/\(.*\)\.in/\1/g')
AC_CONFIG_FILES($MAKEFILES)

AC_OUTPUT

AC_MSG_RESULT(Build configured successfully)
