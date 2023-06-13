package main

import (
  "fmt"
  "os"
  "log"
  "strings"
  "gopkg.in/yaml.v3"
)

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


// --------------- Main ---------------

func main() {
  // Get and check files
  inputFiles := os.Args[1:]
  for _, path := range inputFiles {
    checkFile(path)
  }
  fmt.Println("Hello there", strings.Join(inputFiles, " "))
 
  // Read file
  file, err := os.ReadFile(inputFiles[0])
  reportError("file op: ", err) 

  // Load yaml
  var fileYaml map[string]interface{}
  err = yaml.Unmarshal(file, &fileYaml)
  reportError("yaml: ", err)

  fmt.Println(fileYaml)
}
