
CREATE TABLE `Category`
(
 `category_number` varchar(15) NOT NULL ,
 `category_name`   varchar(45) NOT NULL ,

PRIMARY KEY (`category_number`)
);

CREATE TABLE `Member`
(
 `member_idx` int(11) NOT NULL ,
 `id`         varchar(45) NOT NULL ,
 `passwd`     varchar(45) NOT NULL ,

PRIMARY KEY (`member_idx`)
);

CREATE TABLE `Product`
(
 `product_number`    char(20) NOT NULL ,
 `product_name`      varchar(45) NOT NULL ,
 `product_content`   varchar(1000) NOT NULL ,
 `producer_location` varchar(45) NOT NULL ,
 `capacity_size`     varchar(45) NOT NULL ,
 `nutrient`          varchar(45) NULL ,
 `product_price`     int(11) NOT NULL ,
 `avg_review`        char(4) NOT NULL ,
 `review_count`      int(11) NOT NULL ,
 `category_number`   varchar(15) NOT NULL ,

PRIMARY KEY (`product_number`),
KEY `fkIdx_25` (`category_number`),
CONSTRAINT `FK_category_number` FOREIGN KEY `fkIdx_25` (`category_number`) REFERENCES `Category` (`category_number`)
);


CREATE TABLE `Purchase`
(
 `purchase_idx`   int(11) NOT NULL ,
 `member_idx`     int(11) NOT NULL ,
 `product_number` char(20) NOT NULL ,
 `product_count`  int(11) NOT NULL ,
 `purchase_date`  datetime NOT NULL ,

PRIMARY KEY (`purchase_idx`),
KEY `fkIdx_19` (`product_number`),
CONSTRAINT `FK_19` FOREIGN KEY `fkIdx_19` (`product_number`) REFERENCES `Product` (`product_number`),
KEY `fkIdx_22` (`member_idx`),
CONSTRAINT `FK_22` FOREIGN KEY `fkIdx_22` (`member_idx`) REFERENCES `Member` (`member_idx`)
);