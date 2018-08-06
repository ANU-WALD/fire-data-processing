package main

import (
        "flag"
        "fmt"
        "os/exec"
        "runtime"
        "strings"
	"sync"
)

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

var conc = flag.Int("c", runtime.NumCPU(), "Number of processors.")

func onetileCallGenerator() chan string {
        auTiles := []string{"h28v13","h29v11","h28v12","h29v10","h29v12","h32v10","h27v11",
                            "h31v11","h32v11","h30v11","h30v10","h27v12","h30v12","h31v12",
                            "h31v10","h29v13","h28v11"}

        out := make(chan string)

        go func() {
                defer close(out)
                for _, auTile := range auTiles {
                        out <- fmt.Sprintf("onetile.py --tile %s", auTile)
                }
        }()

        return out
}

func main() {
        flag.Parse()
        cl := NewConcLimiter(*conc)
	tasks := onetileCallGenerator()
        for task := range tasks {
                cl.Increase()
                go func(t string) {
                        fmt.Println("Processing:", t)
                        cmd := exec.Command("/g/data/xc0/software/conda-envs/rs4/bin/python", strings.Split(t, " ")...)
                        _, err := cmd.Output()
                        if err != nil {
                            fmt.Println("Failed:", t)
                            fmt.Println("Submitting again...")
                        go func(tsk string) {
                                tasks <- tsk
                        }(task)
                        }

                        cl.Decrease()
                }(task)
        }
        cl.Wait()
}


