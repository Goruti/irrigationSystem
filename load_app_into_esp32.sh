dir=$PWD
delimiter=$(basename $dir)/


function usage() {
  echo $"Usage: $0 -{first_load | load_all_files | build_bytecode}"
}

function check_loaded_files() {
    echo "Loaded Files"
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 ls"
    eval "$cmd"
}
function build_bytecode() {
  for f in $(find $dir -name '*.py'); do
    string=$f$delimiter

    myarray=()
    while [[ $string ]]; do
      myarray+=( "${string%%"$delimiter"*}" )
      string=${string#*"$delimiter"}
    done
    file=${myarray[*]: -1}
    if [ $file != "boot.py" ] &&\
       [ $file != "main.py" ]; then
      cmd="./mpy-cross $file"
      echo "Generating bytecode for $file with command: $cmd"
      eval "$cmd"
    fi
  done
  echo "all bytecode are generated"
}

function verify_root_directory() {
  if [ $delimiter != "irrigationSystem/" ]; then
    echo "Running Path $dir is not valid. Please run from the Root Folder"
    exit 1
  fi
}
function first_load() {
  for filename in $dir/*; do
    file="$(basename $filename)"
    if [ $file != "README.md" ] &&\
       [ $file != "esp32-20210902-v1.17.bin" ] &&\
       [ $file != "load_app_into_esp32.sh" ]; then
      cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $filename"
      echo "loading $filename with command: $cmd"
      #eval "$cmd"
    fi
  done
  echo "loading is done"
  check_loaded_files
}

function load_all_files() {
   for f in $(find $dir -name 'main.py' -o -name 'boot.py' -o -name '*.mpy' -o -name '*.html.gz' -o -name '*.css.gz'); do
    string=$f$delimiter

    myarray=()
    while [[ $string ]]; do
      myarray+=( "${string%%"$delimiter"*}" )
      string=${string#*"$delimiter"}
    done
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $f ${myarray[*]: -1}"
    echo "loading $f with command: $cmd"
    eval "$cmd"
  done
  echo "loading is done"
  check_loaded_files
}

while [ "$1" != "" ]; do
    case $1 in
        -first_load)
              verify_root_directory
              build_bytecode
              first_load
              exit
              ;;
        -load_all_files)
              verify_root_directory
              build_bytecode
              load_all_files
              exit
              ;;
        -build_bytecode)
          verify_root_directory
          build_bytecode
          exit
          ;;
        -h | --help)
              usage
              exit
              ;;
        *)
              usage
              exit 1
    esac
done