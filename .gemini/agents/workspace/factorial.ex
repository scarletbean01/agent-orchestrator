defmodule Factorial do
  def factorial(0), do: 1
  def factorial(1), do: 1

  def factorial(n) when n > 1 do
    n * factorial(n - 1)
  end
end
