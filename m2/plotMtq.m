data = load('20191210.txt');
%data = load('mtqData.txt');

B0 = data(1, 3);

V = data(2:end, 1);
I = data(2:end, 2);
B = data(2:end, 3);

n = length(V)
n1 = length(I)
n2 = length(B)

B = B - B0;

idx1 = (V > 0);
V1 = V(idx1);
B1 = B(idx1);

idx2 = (V < 0);
V2 = V(idx2);
B2 = B(idx2);

idx3 = (V==0);
V3 = B(idx3);
B3 = B(idx3);


figure(1);
plot(V1, B1, 'r-x');
hold on;
grid on;
plot(V2, B2, 'g-+');
plot(V3, B3, 'b-d');

plot(V1, B1, 'rx');
hold on;
grid on;
plot(V2, B2, 'g+');
plot(V3, B3, 'bd');

%===================
p = polyfit(V, B, 1);
Bfit = polyval(p, V);
plot(V, Bfit, 'y-');

detB = B - Bfit;
s = std(detB)
m = max(B)

A = s/m*100
%===================
pp = polyfit(V1, B1, 1);
Kp = pp(1);

B1fit = polyval(pp, V1);
detB1 = B1 - B1fit;

pm = polyfit(V2, B2, 1);
Km = pm(1);
B2fit = polyval(pm, V2);
detB2 = B2 - B2fit;
%===================
detbm = abs(Kp - Km)/(Kp+Km)/2*100

