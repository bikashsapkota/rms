import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || "Restaurant";

export const metadata: Metadata = {
  title: `${restaurantName} - Fine Dining Experience`,
  description: `Experience exceptional dining at ${restaurantName}. Book your table online for an unforgettable culinary journey.`,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
