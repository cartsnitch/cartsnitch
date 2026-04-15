import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authClient } from "../lib/auth-client.ts";

export function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [resendEmail, setResendEmail] = useState("");
  const [showResend, setShowResend] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendMessage, setResendMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    const callbackURL = searchParams.get("callbackURL") || "/";

    if (!token) {
      setStatus("error");
      return;
    }

    authClient.verifyEmail({ query: { token } })
      .then(() => {
        setStatus("success");
        setTimeout(() => {
          navigate(callbackURL);
        }, 2000);
      })
      .catch(() => {
        setStatus("error");
      });
  }, [searchParams, navigate]);

  async function handleResend() {
    if (!resendEmail) {
      setResendMessage("Please enter your email address.");
      return;
    }

    setResending(true);
    setResendMessage("");

    try {
      const { error } = await authClient.sendVerificationEmail({ email: resendEmail });
      if (error) {
        setResendMessage("Failed to resend. Please try again.");
      } else {
        setResendMessage("Verification email sent!");
        setShowResend(false);
      }
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      {status === "verifying" && (
        <>
          <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-brand-blue" />
          <h1 className="mb-2 text-2xl font-bold text-gray-900">Verifying your email...</h1>
          <p className="text-sm text-gray-500">Please wait while we verify your email address.</p>
        </>
      )}

      {status === "success" && (
        <>
          <h1 className="mb-2 text-2xl font-bold text-gray-900">Email verified!</h1>
          <p className="text-sm text-gray-500">Redirecting you shortly...</p>
        </>
      )}

      {status === "error" && (
        <>
          <h1 className="mb-2 text-2xl font-bold text-gray-900">Verification failed</h1>
          <p className="mb-6 text-sm text-gray-500">The verification link may have expired or is invalid.</p>

          {!showResend ? (
            <button
              type="button"
              onClick={() => setShowResend(true)}
              className="min-h-12 rounded-xl bg-brand-blue px-6 py-3 text-base font-medium text-white active:bg-brand-blue/90"
            >
              Resend verification email
            </button>
          ) : (
            <div className="w-full max-w-sm space-y-4">
              <input
                type="email"
                placeholder="Your email address"
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
                className="min-h-12 w-full rounded-xl border border-gray-200 px-4 text-base focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
              />
              <button
                type="button"
                onClick={handleResend}
                disabled={resending}
                className="min-h-12 w-full rounded-xl bg-brand-blue px-4 py-3 text-base font-medium text-white active:bg-brand-blue/90 disabled:opacity-60"
              >
                {resending ? "Sending..." : "Send verification email"}
              </button>
              {resendMessage && (
                <p className="text-sm text-gray-500">{resendMessage}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
