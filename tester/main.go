package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

// This is how we test schema changes
func main() {
	fmt.Println("Only here for testing")
	connStr := "host=localhost port=26257 user=root dbname=defaultdb sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	// Create a new database
	db.Exec("CREATE DATABASE testdb")
	// Connect to the new database
	connStr = "host=localhost port=26257 user=root dbname=testdb sslmode=disable"
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	// Create a schema
	_, err = db.Exec("CREATE SCHEMA IF NOT EXISTS test_schema")
	if err != nil {
		log.Fatal(err)
	}

	// Create a table in the schema
	_, err = db.Exec("CREATE TABLE test_schema.testtable (id INT, name VARCHAR(255))")
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec("CREATE TABLE test_schema.testtable2 (id INT, name VARCHAR(255), bunch_of_nested_json JSONB)")
	if err != nil {
		log.Fatal(err)
	}

	// Insert a row
	_, err = db.Exec("INSERT INTO test_schema.testtable (id, name) VALUES (1, 'test')")
	if err != nil {
		log.Fatal(err)
	}
}
