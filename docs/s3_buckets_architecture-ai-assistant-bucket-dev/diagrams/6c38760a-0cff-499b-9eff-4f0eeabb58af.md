```mermaid
stateDiagram-v2
    [*] --> Unauthenticated
    Unauthenticated --> Authenticating : login
    Authenticating --> Authenticated : success
    Authenticating --> Unauthenticated : failure
    Authenticated --> LoggedOut : logout
    LoggedOut --> Unauthenticated
    Authenticated --> Authenticated : refresh_token
```