package main

import (
  "fmt"
  "os"
  "log"
  _ "strings"
  "gopkg.in/yaml.v3"
  "errors"
)

type YAML map[interface{}]interface{}

// Throw appropriate error if the file does not exist
func checkFile(path string) {
  _, err := os.Stat(path)
  if err != nil {
    log.SetPrefix("file op: ")
    log.Fatal(fmt.Sprintf("%s is an invalid file path", path))
  }
}


// Temp function to help debugging
func describe(i interface{}) {
	fmt.Printf("(%v, %T)\n", i, i)
}


// Report an error with a prefix and the error contents
func reportError(prefix string, err error) {
  if err == nil { return }
  log.SetPrefix(fmt.Sprintf("ERROR %s", prefix))
  log.Fatal(err)
}

// Read a value from a yaml document 
func (yamlIn YAML) readYaml(keys ...interface{}) (interface{}, error){
  var next interface{} = yamlIn
  for i, key := range keys {
    switch next.(type){
    case YAML:
      switch key.(type) {
      case string:
        next = next.(YAML)[key.(string)]
      case int:
        next = next.(YAML)[key.(int)]
      default:
        return nil, errors.New("string or int indicies only")
      }
    case map[string]interface{}:
      switch key.(type) {
      case string:
        next = next.(map[string]interface{})[key.(string)]
      default:
        return nil, errors.New("cannot use non string for a string key")
      }
    case []interface{}:
      switch key.(type) {
      case string:
        return nil, errors.New("cannot use string to index list") 
      case int:
        next = next.([]interface{})[key.(int)]
      default:
        return nil, errors.New("string or int indicies only")
      }
    default:
      return nil, errors.New("Unknown yaml structure") 
    }
    if next == nil {
      return nil, errors.New("Invalid index")
    }
    if i == len(keys)-1 {
      return next, nil
    }
  }
  return nil, errors.New("internal failure")
}

// --------------- Main ---------------

func main() {
  // Get and check files
  inputFiles := os.Args[1:]
  for _, path := range inputFiles {
    checkFile(path)
  }
  //fmt.Println("Hello there", strings.Join(inputFiles, " "))
 
  // Read file
  var files [][]byte
  for _, path := range inputFiles {
    file, err := os.ReadFile(path)
    files = append(files, file) 
    reportError("file op: ", err) 
  }

  // Load yaml
  var yamls []YAML
  for _, file := range files {
    var yamlFile YAML
    err := yaml.Unmarshal(file, &yamlFile)
    yamls = append(yamls, yamlFile)
    reportError("yaml: ", err)
  }

  data, err := yamls[0].readYaml("INDEX")
  reportError("yaml: ", err)
  value, err := yamls[0].readYaml(data.([]interface{})...)
  reportError("yaml: ", err)

  fmt.Println(value)
}
