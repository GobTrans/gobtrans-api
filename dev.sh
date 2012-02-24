# Check for pip
if ! which pip >/dev/null; then
    echo "Please install pip. 'easy_install pip' usually works."
    exit 1
fi

need_pkg() {
    if ! pip freeze 2>/dev/null | grep -q "^$1=="; then
        echo "Package $1 not installed. Try 'pip install $1'."
        exit 1
    fi
}

# Check if virtualenvwrapper is installed
need_pkg virtualenvwrapper
. `which virtualenvwrapper.sh`

PROJ_DIR=`dirname \`readlink -f "$BASH_SOURCE"\``
PROJ_NAME=`basename $PROJ_DIR`

[ -f "$PROJ_DIR"/deploy/requirements.txt ] && MKENV_OPTS="$MKENV_OPTS -r $PROJ_DIR/deploy/requirements.txt"

if lsvirtualenv | grep -q "^$PROJ_NAME$"; then
    workon "$PROJ_NAME"
else
    mkvirtualenv -a "$PROJ_DIR" $MKENV_OPTS --no-site-packages "$PROJ_NAME"
fi
