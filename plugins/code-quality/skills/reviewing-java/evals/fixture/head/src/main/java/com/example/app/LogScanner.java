package com.example.app;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Counts error lines in log files. */
public class LogScanner {
    public long countAll(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        return lines.size();
    }

    public long countErrors(Path path) throws IOException {
        return Files.lines(path).filter(line -> line.contains("ERROR")).count();
    }

    public long countErrorsIn(List<String> lines) {
        return lines.stream().filter(line -> line.contains("ERROR")).count();
    }
}
