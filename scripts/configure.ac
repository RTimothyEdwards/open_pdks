AC_INIT([open_pdks], [1.0], [github.com/RTimothyEdwards/open_pdks])

# AC_PREFIX_DEFAULT(/usr)
AC_CONFIG_MACRO_DIR(m4)

## REQUIRES: https://www.gnu.org/software/autoconf-archive/ax_python_module.html#ax_python_module
AM_PATH_PYTHON([3.4])
AX_PYTHON_MODULE([distutils],[])

# Check for Mac OS X gsed vs. sed
m4_ifndef([AC_PROG_SED],
    [AC_DEFUN([AC_PROG_SED],[AC_ARG_VAR([SED])
	AC_CHECK_PROGS([SED],[gsed sed])])])

AC_PROG_SED
AC_SUBST(SED)

realpath() {
    # Cross-platform, handles ~
    python3 -c 'import os,sys;print(os.path.realpath(os.path.expanduser(sys.argv@<:@1@:>@)))' $1
}

ENABLED_TECHS=

# Export the open_pdks top level directory
OPENPDKS_TOP=`cd .. && pwd`

# detect PDKs based on directories that include Makefile.in files
m4_define([M4_GET_TECHS], [m4_normalize(m4_esyscmd(cd .. && find -H * -mindepth 1 -maxdepth 1 -name "Makefile.in" -exec dirname {} \; | tr "\n" " "))])

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

        pdkvar[]_ENABLED_VARIANTS="all"
        pdkvar[]_SOURCE_PATH=""
        pdkvar[]_LINK_TARGETS="none"
        pdkvar[]_AUTO="0"

        AC_ARG_ENABLE(pdk-[pdk],
            [AS_HELP_STRING([--enable-pdk-[pdk]=@<:@/path/to/pdk/@:>@ --disable-pdk-[pdk]], "location of the source files for the pdk (pdks with a [pdk]_url file can automatically download them if the path is omitted)")],
            [
                if test "$enableval" == "yes" -o "$enableval" == "YES"; then
                    export pdkvar[]_SOURCE_PATH=../sources/pdk-[pdk]
            	    pdkvar[]_AUTO="1"
		    ENABLED_TECHS="$ENABLED_TECHS pdk"
                elif test "$enableval" == "no" -o "$enableval" == "NO"; then
                    echo "Disabling pdk..."
                else
                    pdkvar[]_SOURCE_PATH=$enableval
		    ENABLED_TECHS="$ENABLED_TECHS pdk"
                fi
            ], [
            ]
        )

        if @<:@ "$[]pdkvar[]_SOURCE_PATH" != "" @:>@; then
            pdkvar[]_SOURCE_PATH=`realpath $[]pdkvar[]_SOURCE_PATH`
            pdkvar[]_BASENAME=`basename $[]pdkvar[]_SOURCE_PATH`
	    if @<:@ "$[]pdkvar[]_BASENAME" = "libraries" @:>@; then
		pdkvar[]_SOURCE_PATH=`dirname $[]pdkvar[]_SOURCE_PATH`
	    fi
            # Basic check that the PDK path exists, unless depending on Makefile
	    # to download it automatically.
            if @<:@ "$[]pdkvar[]_AUTO" = "0" @:>@; then
                AC_MSG_NOTICE([Checking specified path for 'pdk' at $[]pdkvar[]_SOURCE_PATH])
                AC_CHECK_FILE($pdkvar[]_SOURCE_PATH,[
                    AC_MSG_NOTICE(['pdk' source path found at $pdkvar[]_SOURCE_PATH])
                ], [
                    AC_MSG_ERROR([Specified path for 'pdk' at $pdkvar[]_SOURCE_PATH not found])
                ])
	    else
		AC_MSG_NOTICE([PDK 'pdk' will be downloaded automatically during make.])
	    fi

            # --with-pdk-link-targets=PDK_LINK_TARGETS
            AC_ARG_WITH(pdk-link-targets,
                [AS_HELP_STRING([--with-pdk-link-targets=none|source], "make symbolic links to existing files @<:@default=none@:>@")],
                [[]pdkvar[]_LINK_TARGETS=$with_[]pdk[]_link_targets]
            )
            AC_SUBST([]pdkvar[]_LINK_TARGETS)
            AC_MSG_NOTICE([Link targets set to $pdkvar[]_LINK_TARGETS])

            # --with-pdk-variants=PDK_ENABLED_VARIANTS
            AC_ARG_WITH(pdk-variants,
                [AS_HELP_STRING([--with-pdk-variants=all|A|B|...], "compile/install specified PDK variants only @<:@default=all@:>@")],
                [[]pdkvar[]_ENABLED_VARIANTS=$with_[]pdk[]_variants]
            )
            AC_SUBST([]pdkvar[]_ENABLED_VARIANTS)
            AC_MSG_NOTICE([Enabled variants set to $pdkvar[]_ENABLED_VARIANTS])
        fi

        AC_SUBST(pdkvar[]_SOURCE_PATH)
        AC_SUBST(pdkvar[]_LINK_TARGETS)
        AC_SUBST(pdkvar[]_ENABLED_VARIANTS)
    ])
])

AC_MSG_NOTICE([Found technology directories: M4_GET_TECHS()])

M4_GEN_WITH_PDK_ARGS(M4_GET_TECHS())

# Export the list of known technologies to the Makefile
ALL_TECHS="M4_GET_TECHS()"
AC_SUBST(ALL_TECHS)

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
    m4_define([location], $3)

    # echo target targetvar flag location

    targetvar[]_PATH=""

    AC_ARG_ENABLE(
        flag,
        AS_HELP_STRING(
            [--enable-flag@<:@=path@:>@],
            [Install target. If path is omitted, the repository will be downloaded. @<:@default=enabled@:>@]
        ), [
            if test "$enableval" == "yes" -o "$enableval" == "YES"; then
                AC_MSG_NOTICE([Package 'target' will be installed automatically during make.])
        	export targetvar[]_PATH=location/target
            elif test "$enableval" == "no" -o "$enableval" == "NO"; then
                AC_MSG_NOTICE([Disabling package 'target'])
    		export targetvar[]_PATH=""
            else
                targetvar[]_PATH=$enableval
                AC_MSG_NOTICE([Enabling package 'target' at $[]targetvar[]_PATH])
            fi
            targetvar[]_PATH=`realpath $[]targetvar[]_PATH`
        ],[
            AC_MSG_NOTICE([Package 'target' will be installed automatically during make.])
	    targetvar[]_PATH=location/target
	]
    )

    $4

    AC_SUBST(targetvar[]_PATH)
])

# Optional installations (like the above, but disabled by default)
AC_DEFUN([M4_OPT_INSTALLATION], [
    m4_define([target], $1)
    m4_define([targetvar], [m4_normalize(m4_esyscmd(echo target | tr "a-z-" "A-Z_"))])
    m4_define([flag], $2)
    m4_define([location], $3)

    # echo target targetvar flag location

    targetvar[]_PATH=""

    AC_ARG_ENABLE(
        flag,
        AS_HELP_STRING(
            [--enable-flag@<:@=path@:>@],
            [Install target. If path is omitted, the repository will be downloaded. @<:@default=disabled@:>@]
        ), [
            if test "$enableval" == "yes" -o "$enableval" == "YES"; then
                AC_MSG_NOTICE([Package 'target' will be installed automatically during make.])
        	export targetvar[]_PATH=location/target
            elif test "$enableval" == "no" -o "$enableval" == "NO"; then
                AC_MSG_NOTICE([Disabling package 'target'])
    		export targetvar[]_PATH=""
            else
                targetvar[]_PATH=$enableval
                AC_MSG_NOTICE([Enabling package 'target' at $[]targetvar[]_PATH])
            fi
            targetvar[]_PATH=`realpath $[]targetvar[]_PATH`
        ],[
            AC_MSG_NOTICE([Package 'target' will not be installed.])
	]
    )

    $4

    AC_SUBST(targetvar[]_PATH)
])

M4_GEN_INSTALLATION(sky130_ml_xx_hd, alpha-sky130, ../sources)
M4_GEN_INSTALLATION(xschem_sky130, xschem-sky130, ../sources)
M4_GEN_INSTALLATION(klayout_sky130, klayout-sky130, ../sources)
M4_GEN_INSTALLATION(precheck_sky130, precheck-sky130, ../sources)

M4_OPT_INSTALLATION(sky130_sram_macros, sram-sky130, ../sources)
M4_OPT_INSTALLATION(sky130_osu_t12, osu-t12-sky130, ../sources)
M4_OPT_INSTALLATION(sky130_osu_t15, osu-t15-sky130, ../sources)
M4_OPT_INSTALLATION(sky130_osu_t18, osu-t18-sky130, ../sources)

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
# Export the list of enabled technologies to the Makefile
AC_SUBST(ENABLED_TECHS)
# Export the top level directory of open_pdks
AC_SUBST(OPENPDKS_TOP)

MAKEFILES=$(find -L .. -name "Makefile.in" | sed 's/\(.*\)\.in/\1/g')
AC_CONFIG_FILES($MAKEFILES)

AC_OUTPUT

AC_MSG_RESULT(Build configured successfully)
