package main

import (
	"bufio"
	"flag"
	"log"
	"os"
	"time"
	"os/exec"
	"runtime"
	"strings"
	"sync"
)

var conc = flag.Int("c", runtime.NumCPU(), "Number of processors.")
var srcPath = flag.String("i", "files.txt", "Source path for Flint output files.")

type concLimiter struct {
	*sync.WaitGroup
	Pool chan struct{}
}

func (c *concLimiter) Increase() {
	c.Add(1)
	c.Pool <- struct{}{}
}

func (c *concLimiter) Decrease() {
	c.Done()
	<-c.Pool
}

func NewConcLimiter(cLevel int) *concLimiter {
	var wg sync.WaitGroup
	return &concLimiter{&wg, make(chan struct{}, cLevel)}
}

func lfmc_gen(filePath string) chan string {

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

func main() {
	flag.Parse()
	cl := NewConcLimiter(*conc)

	tasks := lfmc_gen(*srcPath)

	for task := range tasks {
		cl.Increase()
		go func(t string) {
			log.Println("Processing:", t)
			args := strings.Split(t, " ")
			for i:=0; i<3; i++ {
				cmd := exec.Command(args[0], args[1:]...)
				_, err := cmd.Output()
				if err == nil {
					break
				}
				log.Printf("%v Retry %s: %d\n", err, t, i+1)
				time.Sleep(time.Duration(4 * (i+1)) * time.Second)
			}
			cl.Decrease()
		}(task)
	}
	cl.Wait()
}
