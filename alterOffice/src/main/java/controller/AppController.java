package controller;


import dto.RegisterRequest;
import dto.RegisterResponse;
import dto.RevokeRequest;
import dto.RevokeResponse;
import entity.RegisteredApp;
import org.springframework.web.bind.annotation.*;
import service.AppService;

@RestController
@RequestMapping("/api/auth")
public class AppController {

    private final AppService appservice;


    public AppController(AppService appservice) {
        this.appservice = appservice;
    }


    @PostMapping("/register")

    public RegisterResponse registerApp(@RequestBody RegisterRequest rrequest){

        RegisteredApp savedApp=appservice.registerApp(rrequest.getAppName(),rrequest.getOwnermail());

        RegisterResponse response=new RegisterResponse();
        response.setApiKey(savedApp.getApiKey());

        return response;
    }

    @GetMapping("/api-key")
    public RegisterResponse getApiKey(@RequestParam String appName){
        String apikey=appservice.getApiKey(appName);

        RegisterResponse response=new RegisterResponse();
        response.setApiKey(apikey);

        return response;
    }


    @PostMapping("/revoke")

    public RevokeResponse revokeResponse(@RequestBody RevokeRequest revokerequest){

        String msg=appservice.revokeApiKey(revokerequest.getApiKey());

        RevokeResponse revokeResponse=new RevokeResponse();

        revokeResponse.setMessage(msg);

        return revokeResponse;
    }



}


