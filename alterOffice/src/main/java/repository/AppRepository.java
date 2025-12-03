package repository;

import entity.RegisteredApp;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AppRepository extends JpaRepository<RegisteredApp, Long> {

    Optional<RegisteredApp> findByOwnerMail(String ownerMail);

    Optional<RegisteredApp> findByApiKey(String apikey);

    Optional<RegisteredApp> findByAppName(String appName);

    boolean existsByApiKey(String apikey);


}
