public class Hello1
{
   public static void Main()
   {

      System.Console.WriteLine("Hello, World!");
      ReadCSVTest();
   }

           public void ReadCSVTest()
        {
            //var msftRaw = Deedle.Frame.ReadCsv(@"C:\dev\222 summary.csv");
            using (StreamReader sr = new StreamReader(@"C:\dev\222 summary.csv"))
            {
                String line;

                while ((line = sr.ReadLine()) != null)
                {
                    string[] parts = line.Split(',');

                    string orderId = parts[0];
                    System.Console.WriteLine(orderId);


                }
            }

        }
}