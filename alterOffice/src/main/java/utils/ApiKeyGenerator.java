package utils;


import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class ApiKeyGenerator {

    public String generateKey(){
        return UUID.randomUUID().toString().replace("-","");
    }
}
