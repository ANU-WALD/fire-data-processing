package main

import (
	"fmt"
	"os/exec"
	"os"
	"flag"
	"sync"
	"log"
	"runtime"
	"strings"
	"bufio"
)

var iFlag = flag.String("i", "./input.txt", "Input file with commands.")

func task_gen(filePath string) <-chan string {

	out := make(chan string)

	go func() {
		defer close(out)

		file, err := os.Open(filePath)
	    if err != nil {
	        log.Fatal(err)
	    }
	    defer file.Close()

	    scanner := bufio.NewScanner(file)
	    for scanner.Scan() {
	        out <- scanner.Text()
	    }

	    if err := scanner.Err(); err != nil {
	        log.Fatal(err)
	    }

	}()

	return out
}

func task_processor(tasks <-chan string) {

	for task := range tasks {
		args := strings.Split(task, " ")
		fmt.Println(args)

		var cmd *exec.Cmd
		cmd = exec.Command(args[0], args[1:]...)

		out, err := cmd.Output()
		if err != nil {
			fmt.Println(err)
		} 

		fmt.Println(string(out))

	}

}


func main() {
	flag.Parse()
	tasks := task_gen(*iFlag)
	var wg sync.WaitGroup
	numWorkers := runtime.NumCPU()
	wg.Add(numWorkers)
	
	for i := 0; i < numWorkers; i++ {
		go func() {
			task_processor(tasks)
			wg.Done()
		}()
	}
	wg.Wait()
	

}
