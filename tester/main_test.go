package main

import (
	"database/sql"
	"fmt"
	"testing"

	_ "github.com/lib/pq"
)

func TestMain(t *testing.T) {
	fmt.Println("Hello, World!")
	db, err := getTestDbConnection()
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}
	defer db.Close()

	sql := "SELECT 1 as one"
	rows, err := db.Query(sql)
	if err != nil {
		t.Fatalf("Failed to query test database: %v", err)
	}
	defer rows.Close()

	sql = "SELECT * FROM test_schema.testtable2 where bunch_of_nested_json->'test'->>'test2' = 'test3'"
	rows, err = db.Query(sql)
	if err != nil {
		t.Fatalf("Failed to query test database: %v", err)
	}
	defer rows.Close()
}

func getTestDbConnection() (*sql.DB, error) {
	connStr := "host=localhost port=26258 user=root dbname=testdb sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
	return db, nil
}
