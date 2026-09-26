package com.example.app;

import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;
import java.util.regex.Pattern;

/** Formats values for every response; each method runs once per request. */
public class Formatter {
    private static final Pattern DIGITS = Pattern.compile("^[0-9]+$");
    private final LinkedList<String> recent = new LinkedList<>();

    public boolean isUpperCase(String value) {
        return Pattern.compile("^[A-Z]+$").matcher(value).matches();
    }

    public boolean isDigits(String value) {
        return DIGITS.matcher(value).matches();
    }

    public String joinAll(List<String> parts) {
        String out = "";
        for (String part : parts) {
            out += part;
            out += ",";
        }
        return out;
    }

    public String joinWithBuilder(List<String> parts) {
        StringBuilder out = new StringBuilder();
        for (String part : parts) {
            out.append(part).append(',');
        }
        return out.toString();
    }

    public String recentAt(int index) {
        return recent.get(index);
    }

    public void remember(String value) {
        recent.add(value);
    }

    /** Inserts a separator after each element through the cursor, which is the list's own strength. */
    public void separate(LinkedList<String> tokens) {
        ListIterator<String> it = tokens.listIterator();
        while (it.hasNext()) {
            it.next();
            it.add("|");
        }
    }
}
