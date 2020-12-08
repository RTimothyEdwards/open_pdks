AC_INIT([open_pdks], [1.0], [github.com/RTimothyEdwards/open_pdks])

# detect PDKs based on directories that include Makefile.in files
m4_define([M4_GET_TECHS], [m4_normalize(m4_esyscmd(cd .. && find * -mindepth 1 -name "Makefile.in" -exec dirname {} \; | tr "\n" " "))])

# check for the source and install paths for each PDK.
AC_DEFUN([M4_GEN_WITH_PDK_ARGS],
[
    # --with-pdk-source=PDK_SOURCE_PATH
    m4_foreach_w(pdk, $1, [
	m4_define([pdkvar], [m4_normalize(m4_esyscmd(echo pdk | tr "a-z" "A-Z"))])
        pdkvar[]_SOURCE_PATH_=""
        AC_ARG_WITH(pdk-source,
              [AS_HELP_STRING([--with-pdk-source=/path/to/pdk/source], "location of the source files for pdk")],
              [pdkvar[]_SOURCE_PATH_=$withval]
        )

	# Require this argument
        AC_MSG_NOTICE([Checking whether source path is specified for 'pdk'])
        if test "x$[]pdkvar[]_SOURCE_PATH_" == "x" ; then
	   AC_MSG_ERROR([Option --with-pdk-source=<path> not specified!])
	fi

	pdkvar[]_SOURCE_PATH=`readlink -f $[]pdkvar[]_SOURCE_PATH_`

        # basic check that the PDK exists there (the path must exist in any case)
        AC_MSG_NOTICE([Checking specified path for 'pdk' at $[]pdkvar[]_SOURCE_PATH])
        AC_CHECK_FILE($[]pdkvar[]_SOURCE_PATH,
        [
           AC_MSG_NOTICE(['pdk' source path found at $[]pdkvar[]_SOURCE_PATH])
        ],
        [
           AC_MSG_ERROR([Specified path for 'pdk' at $[]pdkvar[]_SOURCE_PATH not found])
        ])
        AC_SUBST([]pdkvar[]_SOURCE_PATH)
    ])


    # --with-pdk-local-path=PDK_LOCAL_PATH
    m4_foreach_w(pdk, $1, [
	m4_define([pdkvar], [m4_normalize(m4_esyscmd(echo pdk | tr "a-z" "A-Z"))])
        pdkvar[]_LOCAL_PATH_=""
        AC_ARG_WITH(pdk-local-path,
              [AS_HELP_STRING([--with-pdk-local-path=/path/to/install/pdks], "run-time location of the PDKs")],
              [pdkvar[]_LOCAL_PATH_=$withval]
        )
	# Require this argument
        AC_MSG_NOTICE([Checking whether local path is specified for 'pdk'])
        if test "x$[]pdkvar[]_LOCAL_PATH_" == "x" ; then
	   AC_MSG_ERROR([Option --with-pdk-local-path=<path> not specified!])
	   pdkvar[]_LOCAL_PATH=""
	else
	   pdkvar[]_LOCAL_PATH=`readlink -f $[]pdkvar[]_LOCAL_PATH_`
	fi
        AC_SUBST([]pdkvar[]_LOCAL_PATH)
    ])

    # --with-pdk-dist-path=PDK_DIST_PATH
    m4_foreach_w(pdk, $1, [
	m4_define([pdkvar], [m4_normalize(m4_esyscmd(echo pdk | tr "a-z" "A-Z"))])
        pdkvar[]_DIST_PATH_=""
        AC_ARG_WITH(pdk-dist-path,
              [AS_HELP_STRING([--with-pdk-dist-path=/path/to/install/pdks], "staging location to install the PDKs for distribution (optional)")],
              [pdkvar[]_DIST_PATH_=$withval]
        )
	# Require this argument
        AC_MSG_NOTICE([Checking whether distribution path is specified for 'pdk'])
        if test "x$[]pdkvar[]_DIST_PATH_" == "x" ; then
	   AC_MSG_NOTICE([Option --with-pdk-dist-path=<path> not specified.  Local install only."])
	   pdkvar[]_DIST_PATH=""
	else
	   pdkvar[]_DIST_PATH=`readlink -f $[]pdkvar[]_DIST_PATH_`
	fi
        AC_SUBST([]pdkvar[]_DIST_PATH)
    ])

    # --with-pdk-link-targets=PDK_LINK_TARGETS
    m4_foreach_w(pdk, $1, [
	m4_define([pdkvar], [m4_normalize(m4_esyscmd(echo pdk | tr "a-z" "A-Z"))])
	# Default link_targets = "none"
	pdkvar[]_LINK_TARGETS="none"

        AC_ARG_WITH(pdk-link-targets,
              [AS_HELP_STRING([--with-pdk-link-targets=none|source], "make symbolic links to existing files @<:@default=none@:>@")],
              [[]pdkvar[]_LINK_TARGETS=$with_[]pdk[]_link_targets]
        )
        AC_SUBST([]pdkvar[]_LINK_TARGETS)
        AC_MSG_NOTICE([Link targets set to $[]pdkvar[]_LINK_TARGETS])
    ])
])

AC_MSG_NOTICE([Found technology directories: M4_GET_TECHS()])

M4_GEN_WITH_PDK_ARGS(M4_GET_TECHS())

# Checking if (some) prerequisites are satisfied
AM_PATH_PYTHON([3.4])
AX_PYTHON_MODULE([distutils],[])

AC_PATH_PROG(MAGIC, magic)
if test -z "$MAGIC"; then
   AC_MSG_ERROR([You need 'magic' to generate the needed various cell views])
fi

# Check for "--with-ef-style"
EF_STYLE=0
AC_ARG_WITH([ef-style],
  [AS_HELP_STRING([--with-ef-style],
    [Use efabless style file system structure @<:@default=no@:>@])],
  [
    pdks_ef_style=$withval
    if test "$withval" == "yes" -o "$withval" == "YES"; then
        EF_STYLE=1
    fi
  ], )

AC_SUBST(EF_STYLE)

MAKEFILES=$(find .. -name "Makefile.in" | sed 's/\(.*\)\.in/\1/g')
AC_CONFIG_FILES($MAKEFILES)

AC_OUTPUT

AC_MSG_RESULT(Build configured successfully)
