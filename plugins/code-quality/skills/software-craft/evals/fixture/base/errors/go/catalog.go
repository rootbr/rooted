package shop

import (
	"database/sql"
	"errors"
	"fmt"
)

// Product is one catalogue entry; Price is in cents.
type Product struct {
	ID    string
	Name  string
	Price int64
}

// ErrProductNotFound reports a product id the catalogue does not hold.
var ErrProductNotFound = errors.New("product not found")

// Catalog is the product catalogue. Callers see products and the errors declared in this
// file, never the database behind it.
type Catalog struct {
	db *sql.DB
}

// ProductByID returns the product with the given id, or an error wrapping ErrProductNotFound.
func (c *Catalog) ProductByID(id string) (Product, error) {
	var p Product
	err := c.db.QueryRow(`SELECT id, name, price FROM products WHERE id = ?`, id).Scan(&p.ID, &p.Name, &p.Price)
	if err == sql.ErrNoRows {
		return Product{}, fmt.Errorf("product %s: %w", id, ErrProductNotFound)
	}
	if err != nil {
		return Product{}, fmt.Errorf("product %s: catalogue store failed: %v", id, err)
	}
	return p, nil
}
