## RENAMED Requirements

### Requirement: FileBot satisfies the ChatParticipant protocol
FROM: FileBot satisfies the ChatParticipant protocol
TO: ReadBot satisfies the ChatParticipant protocol

### Requirement: FileBot is pre-configured with read_file and write_file tools
FROM: FileBot is pre-configured with read_file and write_file tools
TO: ReadBot is pre-configured with read_file and list_files tools only

### Requirement: FileBot handles the tool-call round-trip
FROM: FileBot handles the tool-call round-trip
TO: ReadBot handles the tool-call round-trip

### Requirement: FileBot uses file-oriented system instructions
FROM: FileBot uses file-oriented system instructions
TO: ReadBot uses read-oriented system instructions

### Requirement: FileBot reply uses the bot name as sender
FROM: FileBot reply uses the bot name as sender
TO: ReadBot reply uses the bot name as sender

## REMOVED Requirements

### Requirement: FileBot is pre-configured with read_file and write_file tools
**Reason**: ReadBot is read-only. write_file moves to ChangeBot, creating a cleaner pedagogical split between observing the world (ReadBot) and changing it (ChangeBot). The write capability in FileBot conflated two distinct capabilities.
**Migration**: Any config or test referencing FileBot with write_file must be updated. write_file is now exclusively a ChangeBot/AgentBot/GuardBot tool.
