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
	p, err := scanProductRowForCatalog(c.db.QueryRow(`SELECT id, name, price FROM products WHERE id = ?`, id))
	if errors.Is(err, sql.ErrNoRows) {
		return Product{}, fmt.Errorf("product %s: %w", id, ErrProductNotFound)
	}
	if err != nil {
		return Product{}, fmt.Errorf("product %s: catalogue store failed: %v", id, err)
	}
	return p, nil
}

// scanProductRowForCatalog is the catalogue's internal row reader. It wraps the driver
// error for its callers in this file, which translate it before it leaves Catalog.
func scanProductRowForCatalog(row *sql.Row) (Product, error) {
	var p Product
	if err := row.Scan(&p.ID, &p.Name, &p.Price); err != nil {
		return Product{}, fmt.Errorf("scan product row: %w", err)
	}
	return p, nil
}

// PriceOfProductLeaksDriverError returns the current price, in cents, of the product with the given id.
func (c *Catalog) PriceOfProductLeaksDriverError(id string) (int64, error) {
	var price int64
	err := c.db.QueryRow(`SELECT price FROM products WHERE id = ?`, id).Scan(&price)
	if err != nil {
		return 0, fmt.Errorf("price of product %s: %w", id, err)
	}
	return price, nil
}
