/*
 * This is a sample Java file for testing purposes.
 * It contains a simple class with a main method.
 */

public class Sample {
    public static void main(String[] args) {
        String[] names = {"Alice", "Bob", "Charlie", "Diana", "Eve"};
        for (String name : names) {
            System.out.println(greet(name));
        }
    }

    public static String greet(String name) {
        return "Hello, " + name + "!";
    }
}