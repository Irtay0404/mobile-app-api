# Cashierless API

Backend API for autonomous retail stores with AI-powered product recognition and payment processing. Built with FastAPI, OpenAI GPT-4o Vision, PostgreSQL, and Forte Bank integration.

## Features

- 📷 **AI Product Recognition** - Uses OpenAI GPT-4o Vision to identify products from images
- 💳 **Payment Processing** - Integration with Forte Bank for secure payments
- 🔍 **Fuzzy Search** - PostgreSQL with pg_trgm extension for intelligent product matching
- 🌐 **RESTful API** - Clean and documented endpoints
- 🚀 **Async/IO** - Built with asyncpg for high performance

## Architecture

```
mobile-app-api/
├── main.py                 # FastAPI application entry point
├── database.py             # PostgreSQL connection pool & product search
├── schema.sql              # Database schema with pg_trgm indexes
├── seed.sql                # Sample product data
├── routers/
│   ├── recognize.py        # Product recognition endpoints
│   └── checkout.py         # Checkout & payment endpoints
├── services/
│   ├── openai_service.py   # OpenAI GPT-4o Vision integration
│   └── forte_service.py    # Forte Bank payment integration
├── .env.example            # Environment variables template
└── requirements.txt         # Python dependencies
```

## Tech Stack

- **Framework**: FastAPI 0.133.1
- **AI**: OpenAI GPT-4o Vision
- **Database**: PostgreSQL with asyncpg
- **Payment**: Forte Bank API
- **HTTP Client**: httpx

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database
- OpenAI API key
- Forte Bank API credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mobile-app-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
FORTE_BASE_URL=https://sandbox.forte.kz/api/v1
FORTE_API_KEY=your_forte_key
FORTE_MERCHANT_ID=your_merchant_id
NGROK_URL=https://xxxx.ngrok-free.app
```

4. Initialize the database:
```bash
psql -h your-host -U your-user -d your-db -f schema.sql
psql -h your-host -U your-user -d your-db -f seed.sql
```

5. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```
Returns the API status.

### Product Recognition
```
POST /recognize
```
Recognize products from a base64-encoded image.

**Request Body:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "recognized_items": [
    {
      "product_id": 1,
      "name": "Coca-Cola 1L",
      "price": 450.00,
      "quantity": 1,
      "confidence": 0.95
    }
  ],
  "unrecognized": [],
  "total": 450.00
}
```

### Checkout
```
POST /checkout
```
Process payment for cart items.

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "name": "Coca-Cola 1L",
      "price": 450.00,
      "quantity": 1
    }
  ],
  "total": 450.00,
  "card_number": "4111111111111111"
}
```

**Response:**
```json
{
  "order_id": "ORDER-A1B2C3D4",
  "payment": {
    "status": "success",
    "data": {...}
  },
  "items": [...],
  "total": 450.00
}
```

## How It Works

### Recognition Flow

1. **Image Upload**: Client sends base64-encoded image to `/recognize`
2. **Vision Analysis**: OpenAI GPT-4o analyzes the image and identifies visible products
3. **Function Calling**: GPT-4o calls `search_products` tool with product names
4. **Database Search**: Fuzzy search in PostgreSQL using pg_trgm extension
5. **Result Compilation**: GPT-4o formats results with confidence scores and quantities

### Payment Flow

1. **Cart Submission**: Client sends cart items and card details to `/checkout`
2. **Order Generation**: Unique order ID is created
3. **Payment Processing**: Request sent to Forte Bank API
4. **Response**: Payment status and confirmation returned

## Database Schema

### Products Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(255) | Product name |
| name_kz | VARCHAR(255) | Kazakh name |
| category | VARCHAR(100) | Product category |
| description | TEXT | Product description |
| price | NUMERIC(10,2) | Price in KZT |
| image_url | TEXT | Product image URL |
| barcode | VARCHAR(50) | Barcode |
| in_stock | BOOLEAN | Stock availability |
| created_at | TIMESTAMPTZ | Creation timestamp |

## Sample Products

The [`seed.sql`](seed.sql:1) includes sample products:
- Coca-Cola 1L - 450 KZT
- Lay's Сметана 150г - 350 KZT
- Sprite 0.5L - 320 KZT
- Milka Шоколад 90г - 520 KZT
- And more...

## Development

### Running Tests
```bash
pytest
```

### API Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key for GPT-4o | Yes |
| DATABASE_URL | PostgreSQL connection string | Yes |
| FORTE_BASE_URL | Forte Bank API base URL | Yes |
| FORTE_API_KEY | Forte Bank API key | Yes |
| FORTE_MERCHANT_ID | Forte merchant ID | Yes |
| NGROK_URL | Ngrok tunnel URL (optional) | No |

## License

See [`LICENSE`](LICENSE:1) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
