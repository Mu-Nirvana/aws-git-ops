package main

import (
  "fmt"
  "os"
  "log"
  "strings"
  "gopkg.in/yaml.v3"
)

type yamlDoc map[string]interface{}

type Input struct {
  DBName string `yaml:"RDS_DB_NAME"`
  Infra []map[string]string `yaml:"infraConfig"`
}

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

func (yamlIn yamlDoc) readYaml(keys ...string) {
  var next yamlDoc = yamlIn
  fmt.Println(next)
  for _, key := range keys[:len(keys)-1] {
    next = next[key].(yamlDoc)
  }
  fmt.Println(next[keys[len(keys)-1]])
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
  var files [][]byte
  for _, path := range inputFiles {
    file, err := os.ReadFile(path)
    files = append(files, file) 
    reportError("file op: ", err) 
  }

  // Load yaml
  var yamls []Input
  for _, file := range files {
    var yamlFile Input
    err := yaml.Unmarshal(file, &yamlFile)
    yamls = append(yamls, yamlFile)
    reportError("yaml: ", err)
  }

  fmt.Println(yamls)
  fmt.Println(yamls[0].Infra[0]["EKS_CLUSTER"])

  data, _ := yaml.Marshal(yamls[0])
  fmt.Print(string(data))
  //yamls[0].readYaml("infraConfig", "EKS_CLUSTER")
}
