import React from 'react'
import { Container, Navbar, Nav, Card } from 'react-bootstrap'

function App() {
  return (
    <>
      {/* Navigation Bar */}
      <Navbar bg="dark" variant="dark" className="mb-4">
        <Container>
          <Navbar.Brand>Email SaaS Admin</Navbar.Brand>
        </Container>
      </Navbar>

      {/* Main Content */}
      <Container>
        <Card className="p-4">
          <Card.Title>Welcome to your dashboard</Card.Title>
          <Card.Text>
            Here you’ll manage Prospects, Templates, and Sequences.
          </Card.Text>
        </Card>
      </Container>
    </>
  )
}

export default App
