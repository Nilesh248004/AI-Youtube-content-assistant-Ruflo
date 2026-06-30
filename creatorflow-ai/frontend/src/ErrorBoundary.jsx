import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("CreatorFlow UI error", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="fatal-error">
          <div>
            <span>CF</span>
            <p>Something unexpected happened in the interface.</p>
            <button type="button" onClick={() => window.location.reload()}>
              Reload CreatorFlow
            </button>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
