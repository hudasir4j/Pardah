import type { Metadata } from "next";
import { DM_Sans, Instrument_Serif, Italianno, Playfair_Display } from "next/font/google";
import "./globals.css";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: "swap",
});

const instrument = Instrument_Serif({
  variable: "--font-instrument",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  display: "swap",
});

const italianno = Italianno({
  variable: "--font-script",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Kahf — Discover Your Digital Footprint",
  description:
    "A gentle, private tool to help you find and manage your pre-transition digital footprint.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${playfair.variable} ${instrument.variable} ${dmSans.variable} ${italianno.variable} h-full`}
    >
      <body className="kahf-grain kahf-paper min-h-full antialiased">{children}</body>
    </html>
  );
}
