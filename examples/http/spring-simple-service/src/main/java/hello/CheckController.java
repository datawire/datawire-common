package hello;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CheckController {

    @RequestMapping("/greeting/liveness_check")
    public String check() {
        return "OK";
    }
}
