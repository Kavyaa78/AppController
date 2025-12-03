package dto;

public class RegisterRequest {

    private String appName;
    private String ownermail;

    public String getAppName() {
        return appName;
    }

    public void setAppName(String appName) {
        this.appName = appName;
    }

    public String getOwnermail() {
        return ownermail;
    }

    public void setOwnermail(String ownermail) {
        this.ownermail = ownermail;
    }
}
