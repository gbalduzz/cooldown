# usage: update_main.bash [dca_build_root]
DCA_ROOT='../'

if [[ ! -z $1 ]]; then
    DCA_ROOT = $1
fi

make -j -C ${DCA_ROOT}/applications/dca && cp ../applications/dca/main_dca ./
make -j -C ${DCA_ROOT}/applications/analysis && cp ../applications/analysis/main_analysis ./
