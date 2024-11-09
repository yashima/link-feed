CREATE TABLE user (
	id INTEGER AUTO_INCREMENT, 
	username VARCHAR(64) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	is_admin BOOLEAN, 
	last_login DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);
CREATE TABLE user_setting (
	id INTEGER AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	value VARCHAR(50) NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE login_attempts (
	id INTEGER AUTO_INCREMENT, 
	user_id INTEGER, 
	timestamp DATETIME, 
	success BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);

CREATE TABLE link (
       	id INTEGER AUTO_INCREMENT, 
        title VARCHAR(100) NOT NULL,
        domain VARCHAR(200) NOT NULL,
        url_path VARCHAR(200),
        url_params VARCHAR(200)
        summary VARCHAR(500),
        comment VARCHAR(200),
        private BOOLEAN,
        created_at DATETIME,
        secret_link VARCHAR(16) NOT NULL,
        user_id INTEGER,
        PRIMARY KEY (id),
        CONSTRAINT _user_url_ UNIQUE (user_id, url_path, domain,url_params),
        UNIQUE (secret_link),
        FOREIGN KEY(user_id) REFERENCES user (id)
);

CREATE TABLE tag (
        id INTEGER AUTO_INCREMENT, 
        name VARCHAR(50) NOT NULL,
        private BOOLEAN,
        organizational BOOLEAN,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT _user_tag_uc UNIQUE (user_id, name),
        FOREIGN KEY(user_id) REFERENCES user (id)
);

CREATE TABLE link_tags (
        link_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (link_id, tag_id),
        FOREIGN KEY(link_id) REFERENCES link (id),
        FOREIGN KEY(tag_id) REFERENCES tag (id)
);

