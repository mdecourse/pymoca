model DelayForLoop
  Real[2] x, y, a;
  input Real z[2];
  input Real delay_time(fixed=true);
equation
  for i in 1:2 loop
    x[i] = 5 * z[i];
    y[i] = delay(3 * a[i], delay_time);
  end for;
  a = x;
end DelayForLoop;
