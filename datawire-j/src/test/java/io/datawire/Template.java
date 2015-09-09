package io.datawire;

public class Template {
    private String template;
    public Template(String template) {
        this.template = template;
    }
    public String render(int param) {
        return String.format(template, param);
    }
}
