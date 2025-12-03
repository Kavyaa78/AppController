package service;

import entity.RegisteredApp;
import org.springframework.stereotype.Service;
import repository.AppRepository;
import utils.ApiKeyGenerator;

import java.time.LocalDateTime;


@Service
public class AppService {

    private final AppRepository apprepo;
    private final ApiKeyGenerator apikeygen;


    public AppService(AppRepository apprepo, ApiKeyGenerator apikeygen) {
        this.apprepo = apprepo;
        this.apikeygen = apikeygen;
    }


    public RegisteredApp registerApp(String appName, String ownerMail){

        String apiKey=apikeygen.generateKey();

        RegisteredApp regapp=new RegisteredApp();

        regapp.setAppName(appName);
        regapp.setApiKey(apiKey);
        regapp.setActive(true);
        regapp.setOwnerMail(ownerMail);
        regapp.setCreatedAt(LocalDateTime.now());

        return apprepo.save(regapp);

    }

    public String getApiKey(String appName){
        RegisteredApp rapp=apprepo.findByAppName(appName).orElseThrow(()->new RuntimeException("App not found"));

        return rapp.getApiKey();
    }

    public String revokeApiKey(String apikey){

        RegisteredApp app=apprepo.findByApiKey(apikey).orElseThrow(()->new RuntimeException("Invalid API key"));

        app.setActive(false);

        apprepo.save(app);

        return "API revoked successfully";
    }

}


