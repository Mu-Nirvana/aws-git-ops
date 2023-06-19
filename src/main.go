package main

import (
  "fmt"
  "os"
  "log"
  "gopkg.in/yaml.v3"
  "errors"
)

type MAP map[interface{}]interface{}
type LIST = []interface{}
type STRMAP = map[string]interface{}

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


func readNode(key interface{}, node interface{}) (interface{}, error) {
  switch node.(type) {
  case MAP:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      return node.(MAP)[key.(string)], nil
    case int:
      return node.(MAP)[key.(int)], nil
    default:
      return nil, errors.New("string or int indicies only")
    }
  case STRMAP:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      return node.(STRMAP)[key.(string)], nil
    default:
      return nil, errors.New("cannot use non string for a string key")
    }
  case LIST:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      return nil, errors.New("cannot use string to index list") 
    case int:
      return node.(LIST)[key.(int)], nil
    default:
      return nil, errors.New("string or int indicies only")
    }
  default:
    return nil, errors.New("Unknown yaml structure") 
  }
}


/*// Read a value from a yaml document 
func (yamlIn MAP) readYaml(keys ...interface{}) (interface{}, error){
  var next interface{} = yamlIn
  var err error = nil
  // Iterate over passed in keys/indicies
  for i, key := range keys {
    next, err = readNode(key, next)
    if err != nil {
      return nil, err
    }
    if next == nil {
      return nil, errors.New("Invalid index")
    }
    // If this is the last key return the value
    if i == len(keys)-1 {
      return next, nil
    }
  }
  return nil, errors.New("internal failure")
}*/

func readYaml(yamlIn interface{}, keys ...interface{}) (interface{}, error) {
  if len(keys) == 1 {
    value, err := readNode(keys[0], yamlIn)
    if err != nil {
      return nil, err
    }
    return value, nil
  }
  next, err := readNode(keys[0], yamlIn)
  if err != nil {
    return nil, err
  }
  return readYaml(next, keys[1:]...)
}

func writeYaml(yamlIn interface{}, writeValue interface{}, keys ...interface{}) (interface{}, error) {
  if len(keys) == 1 {
    value, err := readNode(keys[0], yamlIn)
    if err != nil {
      return nil, err
    }
    switch value.(type) {
    case string:
      _, ok := writeValue.(string)
      if !ok {
        return nil, errors.New("Cannot write non string to a string field")
      }
      switch keys[0].(type) {
      case string:
        yamlIn.(map[string]string)[keys[0].(string)] = writeValue.(string)
        return yamlIn, nil
      case int:
        yamlIn.(map[int]string)[keys[0].(int)] = writeValue.(string)
        return yamlIn, nil
      }
    case int:
      _, ok := writeValue.(int)
      if !ok {
        return nil, errors.New("Cannot write non int to a int field")
      }
      switch keys[0].(type) {
      case string:
        yamlIn.(map[string]int)[keys[0].(string)] = writeValue.(int)
        return yamlIn, nil
      case int:
        yamlIn.(map[int]int)[keys[0].(int)] = writeValue.(int)
        return yamlIn, nil
      }
    default:
      return nil, errors.New("Can only write to values that are strings or integers")
    }
  }

  switch yamlIn.(type) {
  case MAP:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      yamlIn.(MAP)[key.(string)], nil
    case int:
      return node.(MAP)[key.(int)], nil
    default:
      return nil, errors.New("string or int indicies only")
    }
  case STRMAP:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      return node.(STRMAP)[key.(string)], nil
    default:
      return nil, errors.New("cannot use non string for a string key")
    }
  case LIST:
    // Choose whether the key is a string or int to assertate the type and get the next strucutre
    switch key.(type) {
    case string:
      return nil, errors.New("cannot use string to index list") 
    case int:
      return node.(LIST)[key.(int)], nil
    default:
      return nil, errors.New("string or int indicies only")
    }
  default:
    return nil, errors.New("Unknown yaml structure") 
  }
  yamlIn = writeYaml

    

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
  var yamls []MAP
  for _, file := range files {
    var yamlFile MAP
    err := yaml.Unmarshal(file, &yamlFile)
    yamls = append(yamls, yamlFile)
    reportError("yaml: ", err)
  }

  data, err := readYaml(yamls[0], "INDEX")
  reportError("yaml: ", err)
  _ = data
  value, err := readYaml(yamls[0], data.(LIST)...)
  fmt.Println("second")
  reportError("yaml: ", err)
  fmt.Println(value)
}
