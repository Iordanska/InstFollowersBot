CREATE TABLE users(
    id VARCHAR(255) PRIMARY KEY,
    inst VARCHAR(255),
    vk VARCHAR(255),
    youtube VARCHAR(255)
);

CREATE TABLE inst_stat(
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255),
    followers INTEGER,
    created DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

